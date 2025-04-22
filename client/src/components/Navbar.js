import { Link, useMatch, useResolvedPath } from "react-router-dom";
import "./Navbar.css";
import logo from "../assets/logo.png";

export const Navbar = () => {
  return (
    <nav className="nav">
      <Link to="/HomePage" className="site-title">
        <img src={logo} alt="Just Pick Logo" className="logo" />
        <span className="site-text">Just Pick</span>
      </Link>
      <ul>
        <CustomLink to="/search">Search</CustomLink>
        <CustomLink to="/profile">Profile</CustomLink>
      </ul>
    </nav>
  );
};

// CustomLink as a const arrow function
const CustomLink = ({ to, children, ...props }) => {
  const resolvedPath = useResolvedPath(to);
  const isActive = useMatch({ path: resolvedPath.pathname, end: true });

  return (
    <li className={isActive ? "active" : ""}>
      <Link to={to} {...props}>
        {children}
      </Link>
    </li>
  );
};

export default Navbar;
