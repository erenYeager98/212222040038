import axios from "axios";

const LOGGING_API = "http://20.244.56.144/evaluation-service/logs"; // or your local for testing

export async function logEvent(stack, level, pkg, message) {
  try {
    await axios.post(
      LOGGING_API,
      {
        stack,     // "frontend"
        level,     // "info", "warn", "error", "debug", "fatal"
        package: pkg,  // "api", "page", "hook", etc.
        message
      }
    );
  } catch (err) {
    // Fallback to console.error if logging server is unreachable
    console.error("Logging failed:", err.message);
  }
}
