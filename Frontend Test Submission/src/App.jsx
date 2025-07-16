import React from "react";
import { Container, Tabs, Tab, Box } from "@mui/material";
import ShortenerForm from "./components/ShortenerForm";
import StatsPage from "./components/StatsPage";

export default function App() {
  const [tab, setTab] = React.useState(0);

  return (
    <Container>
      <Box sx={{ borderBottom: 1, borderColor: "divider", mt: 4 }}>
        <Tabs value={tab} onChange={(_, val) => setTab(val)}>
          <Tab label="Shorten URL" />
          <Tab label="View Stats" />
        </Tabs>
      </Box>
      <Box sx={{ mt: 4 }}>
        {tab === 0 ? <ShortenerForm /> : <StatsPage />}
      </Box>
    </Container>
  );
}
