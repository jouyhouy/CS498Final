import React from 'react';
import { Container } from 'reactstrap';

const Footer: React.FC = () => {
    return (
        <footer className="bg-gray-800 text-white py-4 mt-8">
            <Container className="text-center">
                <p>&copy; University of Illinois</p>
            </Container>
        </footer>
    );
};

export default Footer;