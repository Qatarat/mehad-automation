/**
 * WhatsApp OTP Bridge Server
 * ─────────────────────────
 * Free, open-source alternative to Twilio for reading production OTPs.
 * Uses whatsapp-web.js (MIT) to connect a WhatsApp account via QR scan
 * and expose a local HTTP endpoint that returns the latest 6-digit OTP.
 *
 * Setup (one-time):
 *   cd scripts && npm install
 *   node whatsapp_otp_server.js
 *   → Scan the QR code with your test WhatsApp account
 *   → Session saved to .wwebjs_auth/ (no QR needed on next run)
 *
 * Then set in .env:
 *   PROD_OTP_BACKEND=whatsapp_local
 *   WA_OTP_PORT=3001          # optional, default 3001
 *
 * The get_otp.py script polls GET http://localhost:3001/otp until OTP arrives.
 */

const { Client, LocalAuth } = require("whatsapp-web.js");
const qrcode = require("qrcode-terminal");
const http = require("http");

const PORT = parseInt(process.env.WA_OTP_PORT || "3001", 10);
const OTP_TTL_MS = 3 * 60 * 1000; // ignore messages older than 3 min

// Ring buffer — keep last 30 OTP messages
const otpBuffer = [];

const client = new Client({
  authStrategy: new LocalAuth({ dataPath: ".wwebjs_auth" }),
  puppeteer: {
    headless: true,
    args: ["--no-sandbox", "--disable-setuid-sandbox"],
  },
});

client.on("qr", (qr) => {
  console.log("\n[WA] Scan this QR code with your test WhatsApp account:\n");
  qrcode.generate(qr, { small: true });
});

client.on("authenticated", () => {
  console.log("[WA] Authenticated — session saved.");
});

client.on("ready", () => {
  console.log(`[WA] WhatsApp client ready. OTP server listening on :${PORT}`);
});

client.on("auth_failure", (msg) => {
  console.error("[WA] Auth failed:", msg);
  process.exit(1);
});

client.on("message", (msg) => {
  const body = msg.body || "";
  const match = body.match(/\b(\d{6})\b/);
  if (match) {
    const entry = { otp: match[1], from: msg.from, body, ts: Date.now() };
    otpBuffer.unshift(entry);
    if (otpBuffer.length > 30) otpBuffer.pop();
    console.log(`[WA] OTP captured: ${entry.otp} (from ${entry.from})`);
  }
});

client.initialize();

// ── HTTP server ────────────────────────────────────────────────────────────

const server = http.createServer((req, res) => {
  res.setHeader("Content-Type", "application/json");

  if (req.url === "/otp" && req.method === "GET") {
    // Return the most recent OTP received within TTL
    const recent = otpBuffer.find((e) => Date.now() - e.ts < OTP_TTL_MS);
    if (recent) {
      res.writeHead(200);
      res.end(JSON.stringify({ otp: recent.otp, from: recent.from, ts: recent.ts }));
    } else {
      res.writeHead(404);
      res.end(JSON.stringify({ otp: null, message: "No OTP received yet" }));
    }
    return;
  }

  if (req.url === "/clear" && req.method === "POST") {
    // Clear the buffer between test runs so stale OTPs aren't reused
    otpBuffer.length = 0;
    res.writeHead(200);
    res.end(JSON.stringify({ cleared: true }));
    return;
  }

  if (req.url === "/health") {
    res.writeHead(200);
    res.end(JSON.stringify({ status: "ok", buffered: otpBuffer.length }));
    return;
  }

  res.writeHead(404);
  res.end(JSON.stringify({ error: "Not found" }));
});

server.listen(PORT, "127.0.0.1", () => {
  console.log(`[WA] OTP HTTP bridge: http://127.0.0.1:${PORT}/otp`);
});
