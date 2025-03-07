import "./App.css";
//import React, { useEffect, useState } from 'react';
import { BrowserRouter, Routes, Route } from "react-router-dom";
import {Login} from "./components/Login.js";
import {Registration} from "./components/Registration.js";
import { Searchbar } from "./searchbar.js";

export function App() {
  /* const [data, setData] = useState(null);

useEffect(() => {
  fetch('http://127.0.0.1:5000/api/data')
      .then(response => response.json())
      .then(data => setData(data.message))
      .catch(error => console.error("Error fetching data:", error));
}, []); */

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/Login" element={<Login />}></Route>
        <Route path="/Registration" element={<Registration />}></Route>
        <Route path="/search" element={<Searchbar/>}></Route>
      </Routes>
    </BrowserRouter>
  );
}


