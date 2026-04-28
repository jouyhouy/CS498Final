import React from "react";
import { Navbar as ReactstrapNavbar, NavbarBrand } from "reactstrap";

const Navbar: React.FC = () => {
    return (
        <ReactstrapNavbar light color="light" expand="md">
            <NavbarBrand href="/">CS 498</NavbarBrand>
        </ReactstrapNavbar>
    );
};

export default Navbar;