import { Routes, Route } from "react-router-dom";
import LoginPanel from "./components/Login/Login";
import Register from "./components/Register/Register"; // <-- Import Register component

function App() {
  return (
    <Routes>
      {/* Route for the Login page */}
      <Route path="/login" element={<LoginPanel />} />

      {/* Route for the Register page */}
      <Route path="/register" element={<Register />} />

      {/* You may also add a default/Home route if needed */}
      {/* <Route path="/" element={<Home />} /> */}
    </Routes>
  );
}

export default App;
