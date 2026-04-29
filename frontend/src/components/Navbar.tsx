import React from "react";
import { Navbar as ReactstrapNavbar, NavbarBrand } from "reactstrap";
import { Link } from "react-router"

const Navbar: React.FC = () => {
    return (
        <ReactstrapNavbar light color="light" expand="md">
            <NavbarBrand tag={Link} to="/">CS 498</NavbarBrand>
        </ReactstrapNavbar>
    );
};

export default Navbar;