import { SESv2Client, SendEmailCommand } from "@aws-sdk/client-sesv2";

const ses = new SESv2Client({ region: "us-east-1" });

const TO = ["alison@healthgardenadvocacy.com", "mtompkins82@gmail.com"];
const FROM = "Healthgarden Website <noreply@healthgardenadvocacy.com>";
const ALLOWED_ORIGIN = "https://healthgardenadvocacy.com";

const headers = {
  "Access-Control-Allow-Origin": ALLOWED_ORIGIN,
  "Access-Control-Allow-Methods": "POST, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type",
  "Content-Type": "application/json",
};

function reply(statusCode, body) {
  return { statusCode, headers, body: JSON.stringify(body) };
}

function clean(value, max) {
  if (typeof value !== "string") return "";
  return value.replace(/[\r\n]+/g, " ").trim().slice(0, max);
}

export const handler = async (event) => {
  const method = event.requestContext?.http?.method;

  if (method === "OPTIONS") return reply(204, {});
  if (method !== "POST") return reply(405, { error: "Method not allowed" });

  let data;
  try {
    data = JSON.parse(event.body || "{}");
  } catch {
    return reply(400, { error: "Invalid request" });
  }

  if (clean(data.company, 100)) {
    return reply(200, { ok: true });
  }

  const name = clean(data.name, 100);
  const email = clean(data.email, 200);
  const phone = clean(data.phone, 50);
  const inquiry = clean(data.inquiry, 100);
  const message = typeof data.message === "string" ? data.message.trim().slice(0, 5000) : "";

  if (!name || !email || !inquiry) {
    return reply(400, { error: "Please fill in the required fields." });
  }

  if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) {
    return reply(400, { error: "Please enter a valid email address." });
  }

  const body = [
    `Name: ${name}`,
    `Email: ${email}`,
    `Phone: ${phone || "(not provided)"}`,
    `Nature of inquiry: ${inquiry}`,
    "",
    "Message:",
    message || "(none)",
  ].join("\n");

  try {
    await ses.send(new SendEmailCommand({
      FromEmailAddress: FROM,
      Destination: { ToAddresses: Array.isArray(TO) ? TO : [TO] },
      ReplyToAddresses: [email],
      Content: {
        Simple: {
          Subject: { Data: `Healthgarden inquiry — ${name}` },
          Body: { Text: { Data: body } },
        },
      },
    }));
    return reply(200, { ok: true });
  } catch (err) {
    console.error("SES send failed:", err);
    return reply(500, { error: "Something went wrong. Please try again or email directly." });
  }
};
