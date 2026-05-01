import React from 'react';
import { Container } from 'reactstrap';

const Footer: React.FC = () => {
    return (
        <footer className="bg-light py-3 app-footer">
            <Container className="text-center">
                <p style={{color: "black"}}>&copy; University of Illinois</p>
            </Container>
        </footer>
    );
};

export default Footer;