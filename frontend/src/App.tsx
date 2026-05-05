import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";

import { ActivityPage } from "./pages/ActivityPage";
import { AssetsPipelinePage } from "./pages/AssetsPipelinePage";
import { CampaignsPage } from "./pages/CampaignsPage";
import { HomePage } from "./pages/HomePage";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/assets" element={<AssetsPipelinePage />} />
        <Route path="/collectibles" element={<CampaignsPage />} />
        <Route path="/activity" element={<ActivityPage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
