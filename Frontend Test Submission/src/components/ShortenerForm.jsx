import React, { useState } from "react";
import { logEvent } from "../../../Logging Middleware/logger";

import {
  Box,
  TextField,
  Button,
  Typography,
  Grid,
  Alert
} from "@mui/material";
import axios from "axios";

export default function ShortenerForm() {
  const [inputs, setInputs] = useState([{ url: "", validity: "", shortcode: "" }]);
  const [results, setResults] = useState([]);
  const [error, setError] = useState("");

  const handleInputChange = (index, key, value) => {
    const updated = [...inputs];
    updated[index][key] = value;
    setInputs(updated);
  };

  const addMore = () => {
    if (inputs.length < 5) {
      setInputs([...inputs, { url: "", validity: "", shortcode: "" }]);
    }
  };

  const handleSubmit = async () => {
    try {
      const all = await Promise.all(
        inputs.map((data) =>
          axios.post("http://localhost:8000/shorturls", {
            url: data.url,
            validity: parseInt(data.validity) || 30,
            shortcode: data.shortcode || undefined
          })
        )
      );
      setResults(all.map((res) => res.data));
      setError("");
    } catch (err) {
      setError(err?.response?.data?.detail || "Something went wrong");
    }
  };

  return (
    <Box>
      {inputs.map((input, idx) => (
        <Grid container spacing={2} key={idx} sx={{ mb: 2 }}>
          <Grid item xs={12} sm={6}>
            <TextField
              label="Original URL"
              fullWidth
              value={input.url}
              onChange={(e) => handleInputChange(idx, "url", e.target.value)}
              required
            />
          </Grid>
          <Grid item xs={3} sm={2}>
            <TextField
              label="Validity (min)"
              type="number"
              fullWidth
              value={input.validity}
              onChange={(e) => handleInputChange(idx, "validity", e.target.value)}
            />
          </Grid>
          <Grid item xs={3} sm={4}>
            <TextField
              label="Custom Shortcode"
              fullWidth
              value={input.shortcode}
              onChange={(e) => handleInputChange(idx, "shortcode", e.target.value)}
            />
          </Grid>
        </Grid>
      ))}
      <Button variant="contained" onClick={handleSubmit}>Shorten</Button>
      <Button onClick={addMore} sx={{ ml: 2 }} disabled={inputs.length >= 5}>
        + Add Another
      </Button>
      {error && <Alert severity="error" sx={{ mt: 2 }}>{error}</Alert>}
      <Box sx={{ mt: 3 }}>
        {results.map((res, idx) => (
          <Box key={idx} sx={{ mb: 2 }}>
            <Typography>Shortened URL: <a href={res.shortLink} target="_blank">{res.shortLink}</a></Typography>
            <Typography>Expires at: {res.expiry}</Typography>
          </Box>
        ))}
      </Box>
    </Box>
  );
}
