// SPDX-License-Identifier: Apache-2.0
import './main.css';
import { BrowserRouter, Routes, Route } from "react-router-dom";

import Home from "@/pages/Home";
import PromptPage from "@/pages/PromptPage";
import RankResultPage from "@/pages/RankResultPage";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/prompt" element={<PromptPage />} />
        <Route path="/rank-result" element={<RankResultPage />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;