import React from "react";
import { Link } from "react-router";
import {
    Container,
    Row,
    Col,
    Card,
    CardBody,
    CardTitle,
    CardText,
    Button,
} from "reactstrap";

const Home: React.FC = () => {
    return (
        <Container className="py-4">
            <Row className="mb-4">
                <Col>
                    <h1>Twitter 2018 Eurovision Final Dataset Explorer</h1>
                </Col>
            </Row>

            <Row className="align-items-stretch">
                <Col md={6} lg={4}>
                    <Card className="h-100">
                        <CardBody className="d-flex flex-column">
                            <CardTitle tag="h5">Explore Tweets</CardTitle>
                            <CardText>
                                Navigate to a table view that lists tweets (tweet-by-tweet).
                                This is a placeholder card — the table route and component can
                                be implemented separately.
                            </CardText>
                            <Button color="primary" className="mt-auto" tag={Link} to="/tweets">
                                Open Tweet Table
                            </Button>
                        </CardBody>
                    </Card>
                </Col>

                <Col md={6} lg={4}>
                    <Card className="h-100">
                        <CardBody className="d-flex flex-column">
                            <CardTitle tag="h5">Most Active Countries</CardTitle>
                            <CardText>View the top countries that have the most tweets!</CardText>
                            <Button color="secondary" className="mt-auto" tag={Link} to="/top-countries">
                                Go to Top Countries
                            </Button>
                        </CardBody>
                    </Card>
                </Col>

                <Col md={6} lg={4}>
                    <Card className="h-100">
                        <CardBody className="d-flex flex-column">
                            <CardTitle tag="h5">Visualizations</CardTitle>
                            <CardText>Placeholder for charts and other visual components.</CardText>
                            <Button color="info" className="mt-auto" tag={Link} to="/visualizations">
                                View Visualizations
                            </Button>
                        </CardBody>
                    </Card>
                </Col>
            </Row>
        </Container>
    );
};

export default Home;