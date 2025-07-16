import React, { useState } from "react";
import {
  Box,
  TextField,
  Button,
  Typography,
  Alert
} from "@mui/material";
import axios from "axios";

export default function StatsPage() {
  const [shortcode, setShortcode] = useState("");
  const [stats, setStats] = useState(null);
  const [error, setError] = useState("");

  const fetchStats = async () => {
    try {
      const res = await axios.get(`http://localhost:8000/shorturls/${shortcode}`);
      setStats(res.data);
      setError("");
    } catch (err) {
      setError(err?.response?.data?.detail || "Error fetching stats");
    }
  };

  return (
    <Box>
      <TextField
        label="Enter Shortcode"
        fullWidth
        value={shortcode}
        onChange={(e) => setShortcode(e.target.value)}
      />
      <Button variant="contained" sx={{ mt: 2 }} onClick={fetchStats}>
        Get Stats
      </Button>
      {error && <Alert severity="error" sx={{ mt: 2 }}>{error}</Alert>}
      {stats && (
        <Box sx={{ mt: 4 }}>
          <Typography>Original URL: {stats.original_url}</Typography>
          <Typography>Created At: {stats.created_at}</Typography>
          <Typography>Expires At: {stats.expiry_at}</Typography>
          <Typography>Total Clicks: {stats.clicks}</Typography>
          <Box sx={{ mt: 2 }}>
            <Typography variant="h6">Click History:</Typography>
            {stats.click_data.map((c, i) => (
              <Box key={i} sx={{ mb: 1 }}>
                <Typography variant="body2">
                  Time: {c.timestamp}, IP: {c.ip}, Location: {c.location}, Referrer: {c.referrer}
                </Typography>
              </Box>
            ))}
          </Box>
        </Box>
      )}
    </Box>
  );
}
