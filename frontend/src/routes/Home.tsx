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

      <Row className="align-items-stretch g-3">
        <Col md={6} lg={4}>
          <Card className="h-100">
            <CardBody className="d-flex flex-column">
              <CardTitle tag="h5">Most Active Countries</CardTitle>
              <CardText>
                View the top countries that have the most tweets!
              </CardText>
              <Button
                color="primary"
                className="mt-auto"
                tag={Link}
                to="/top-countries"
              >
                Go to Top Countries
              </Button>
            </CardBody>
          </Card>
        </Col>
        <Col md={6} lg={4}>
          <Card className="h-100">
            <CardBody className="d-flex flex-column">
              <CardTitle tag="h5">View Tweets by User</CardTitle>
              <CardText>View tweets by a specific user.</CardText>
              <Button
                color="primary"
                className="mt-auto"
                tag={Link}
                to="/tweets-by-user"
              >
                View Tweets by User
              </Button>
            </CardBody>
          </Card>
        </Col>
        <Col md={6} lg={4}>
          <Card className="h-100">
            <CardBody className="d-flex flex-column">
              <CardTitle tag="h5">View Most Active Users</CardTitle>
              <CardText>View the most active users regarding the dataset.</CardText>
              <Button
                color="primary"
                className="mt-auto"
                tag={Link}
                to="/most-active-users"
              >
                View Most Active Users
              </Button>
            </CardBody>
          </Card>
        </Col>
        <Col md={6} lg={4}>
          <Card className="h-100">
            <CardBody className="d-flex flex-column">
              <CardTitle tag="h5">View Top Hashtags</CardTitle>
              <CardText>View the most popular hashtags in the dataset.</CardText>
              <Button
                color="primary"
                className="mt-auto"
                tag={Link}
                to="/top-hashtags"
              >
                View Top Hashtags
              </Button>
            </CardBody>
          </Card>
        </Col>
        <Col md={6} lg={4}>
          <Card className="h-100">
            <CardBody className="d-flex flex-column">
              <CardTitle tag="h5">Engagement Breakdown</CardTitle>
              <CardText>
                View the breakdown of engagements (retweets, quotes, replies) by verified users.
              </CardText>
              <Button
                color="primary"
                className="mt-auto"
                tag={Link}
                to="/engagement-breakdown"
              >
                View Engagement Breakdown
              </Button>
            </CardBody>
          </Card>
        </Col>
      </Row>
    </Container>
  );
};

export default Home;
