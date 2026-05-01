import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  Alert,
  Button,
  Card,
  CardBody,
  Container,
  Form,
  Input,
  Row,
  Spinner,
} from "reactstrap";
import axios from "axios";
import type { TweetDocument } from "../models/Tweets";

const fetchTweetsByUser = async (
  username: string,
): Promise<TweetDocument[]> => {
  try {
    const response = await axios.get("/tweets-by-user", {
      params: { username },
    });
    return response.data as TweetDocument[];
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
  } catch (error: any) {
    throw new Error("an error occurred while fetching tweets by user", {
      cause: error,
    });
  }
};

const UserTweets = (): React.JSX.Element => {
  const [usernameInput, setUsernameInput] = useState("");
  const [username, setUsername] = useState("");

  const {
    data = [],
    isFetching,
    error,
  } = useQuery<TweetDocument[], Error>({
    queryKey: ["tweets-by-user", username],
    queryFn: () => fetchTweetsByUser(username),
    enabled: username.length > 0,
    initialData: [],
  });

  const handleSubmit = (event: React.SubmitEvent<HTMLFormElement>) => {
    event.preventDefault();
    setUsername(usernameInput.trim());
  };

  return (
    <Container className="py-4">
      <Form onSubmit={handleSubmit}>
        <Row className="g-2 mb-4">
          <Input
            type="text"
            placeholder="Search by username..."
            value={usernameInput}
            onChange={(event) => setUsernameInput(event.target.value)}
          />
          <Button color="primary" type="submit">
            Search
          </Button>
        </Row>
      </Form>

      {isFetching && (
        <div className="py-4 text-center">
          <Spinner color="primary" />
          <p className="mt-2 mb-0">Loading tweets...</p>
        </div>
      )}

      {error && <Alert color="danger">Error: {error.message}</Alert>}

      {!isFetching && !error && username && data.length === 0 && (
        <Alert color="light">No tweets found for @{username}.</Alert>
      )}

      {!isFetching && (
        <div className="d-flex flex-column gap-3">
          {data.map((tweet) => (
            <Card key={tweet.id}>
              <CardBody>
                <h5>{tweet.text}</h5>
                <p className="mb-0 text-muted">{tweet.created_at}</p>
                <p>
                  <strong>@{tweet.user.screen_name}</strong>
                </p>
                {tweet.in_reply_to_screen_name && (
                  <p>
                    {" "}
                    In reply to:{" "}
                    <strong>@{tweet.in_reply_to_screen_name}</strong>
                  </p>
                )}
              </CardBody>
            </Card>
          ))}
        </div>
      )}
    </Container>
  );
};

export default UserTweets;
