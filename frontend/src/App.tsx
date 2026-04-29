import './App.css'
import { BrowserRouter, Routes, Route } from "react-router"
import Navbar from "./components/Navbar"
import Footer from "./components/Footer"
/** Route Declarations */
import Home from "./routes/Home"
import Tweets from "./routes/Tweets"
import TopCountries from './routes/TopCountries'
/** End Route Declarations */

const App = (): React.JSX.Element => {
  return (
    <BrowserRouter>
      <Navbar />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/tweets" element={<Tweets />} />
        <Route path="/top-countries" element={<TopCountries />} />
      </Routes>
      <Footer />
    </BrowserRouter>
  )
}

export default App
