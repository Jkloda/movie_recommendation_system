import React, {useState, useEffect} from "react";
import { useNavigate } from "react-router-dom";
import { Navbar } from "../components/Navbar.js";
import { SemanticSearchBar } from "../components/SemanticSearchBar.js";
import { PopularMovies } from "../components/PopularMovies.js";
import { SimilarMovies } from "../components/SimilarMovies.js";
export function HomePage({authFlag}) {
  // create state and navigation for auth check (Martin)
  const [checkAuth, setCheckAuth] = useState(undefined)
  const navigate = useNavigate();

  // on mount check server, using session cookie, if user is authenticated (Martin)
  useEffect(() =>{
      async function authenticator(){
        const response = await fetch("https://127.0.0.1:443/check_auth", {
          method: "GET",
          credentials: "include",
        });
        const jsonResponse = await response.json()
        return jsonResponse.authenticated
      }
      async function trigger(){
        let auth = await authenticator()
        setCheckAuth(auth)
      }
      if(authFlag) trigger();
  }, [])

  // side effect to check if user authentication is true and redirect to login if not
  useEffect(() => {
    if(checkAuth != undefined){
      if(checkAuth){
        authFlag(true)
      } else {
        authFlag(false)
        navigate('/login')
      }
    }
  }, [checkAuth])

  return (
    <>
      <Navbar />
      <SemanticSearchBar />
      <SimilarMovies />
      <div>
        <PopularMovies />
      </div>
    </>
  );
}
