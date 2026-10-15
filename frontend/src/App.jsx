import { BrowserRouter, Routes, Route } from "react-router-dom";

import { ChatProvider } from "./context/ChatContext";
import Layout from "./components/Layout";
import Dashboard from "./pages/Dashboard";
import PlayerSearch from "./pages/PlayerSearch";
import PlayerProfile from "./pages/PlayerProfile";
import Predictor from "./pages/Predictor";
import Compare from "./pages/Compare";
import Analytics from "./pages/Analytics";
import Assistant from "./pages/Assistant";

export default function App() {
  return (
    <BrowserRouter>
      <ChatProvider>
        <Routes>
          <Route element={<Layout />}>
            <Route path="/" element={<Dashboard />} />
            <Route path="/search" element={<PlayerSearch />} />
            <Route path="/players/:id" element={<PlayerProfile />} />
            <Route path="/predict" element={<Predictor />} />
            <Route path="/compare" element={<Compare />} />
            <Route path="/analytics" element={<Analytics />} />
            <Route path="/assistant" element={<Assistant />} />
          </Route>
        </Routes>
      </ChatProvider>
    </BrowserRouter>
  );
}
