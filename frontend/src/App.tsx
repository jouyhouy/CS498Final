import './App.css'
import { BrowserRouter, Routes, Route } from "react-router"
import Navbar from "./components/Navbar"

const App = (): React.JSX.Element => {
  return (
    <BrowserRouter>
      <Navbar />
      <Routes>
        <Route path="/" element={<h1>Home</h1>} />
      </Routes>
      {/** Footer goes here */}
    </BrowserRouter>
  )
}

export default App
