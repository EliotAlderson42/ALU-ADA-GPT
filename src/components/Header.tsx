import { Link, useLocation } from "react-router-dom";

function Header() {
  const location = useLocation();
  return (
    <header className="header-nav">
      <Link to="/" className="header-logo">
        ALU/ADA GPT
      </Link>
      <nav className="header-links">
        <Link to="/" className={location.pathname === "/" ? "active" : ""}>
          Accueil
        </Link>
        <Link to="/questions" className={location.pathname === "/questions" ? "active" : ""}>
          Questions
        </Link>
        <Link to="/memoire-technique" className={location.pathname === "/memoire-technique" ? "active" : ""}>
          Memoire technique
        </Link>
      </nav>
    </header>
  );
}

export default Header