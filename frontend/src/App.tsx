import "./App.css";
import { BrowserRouter, Routes, Route } from "react-router";
import Navbar from "./components/Navbar";
import Footer from "./components/Footer";
/** Route Declarations */
import Home from "./routes/Home";
import TopCountries from "./routes/TopCountries";
import TweetsByUser from "./routes/UserTweets";
import MostActiveUsers from "./routes/MostActiveUsers";
import TopHashtags from "./routes/TopHashtags";
import EngagementBreakdown from "./routes/EngagementBreakdown";
/** End Route Declarations */

const App = (): React.JSX.Element => {
  return (
    <BrowserRouter>
      <div className="app-shell">
        <Navbar />
        <main className="app-content">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/top-countries" element={<TopCountries />} />
            <Route path="/tweets-by-user" element={<TweetsByUser />} />
            <Route path="/most-active-users" element={<MostActiveUsers />} />
            <Route path="/top-hashtags" element={<TopHashtags />} />
            <Route path="/engagement-breakdown" element={<EngagementBreakdown />} />
          </Routes>
        </main>
        <Footer />
      </div>
    </BrowserRouter>
  );
};

export default App;
