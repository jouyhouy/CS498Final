import { type JSX } from "react";
import { useQuery } from '@tanstack/react-query';
import axios from "axios";
import { Container, Spinner, Alert, Card, CardBody, CardHeader, Table } from "reactstrap";

interface EngagementBreakdownItem {
    user_name: string;
    screen_name: string;
    total_tweets: number;
    simple_percent: number;
    retweet_percent: number;
    quote_percent: number;
    reply_percent: number;
}

const fetchEngagementBreakdown = async (): Promise<EngagementBreakdownItem[]> => {
    try {
        const response = await axios.get<EngagementBreakdownItem[]>('/engagement-breakdown');
        return response.data;
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
    } catch (error: any) {
        throw new Error("An error occurred while fetching engagement breakdown", {
            cause: error,
        });
    }
}


const EngagementBreakdown = (): JSX.Element => {
    const { data, error, isLoading } = useQuery<EngagementBreakdownItem[]>({
        queryKey: ['engagement-breakdown'],
        queryFn: fetchEngagementBreakdown,
    })

    if (isLoading) {
        return (
            <div className="d-flex flex-column flex-grow-1 justify-content-center align-items-center w-100 py-5">
                <Spinner color="primary" />
                <p>Loading... (this may take a moment)</p>
            </div>
        );
    }

    if (error) {
        return (
            <Container className="mt-4">
                <Alert color="danger">
                    {error instanceof Error ? error.message : 'An unknown error occurred.'}
                </Alert>
            </Container>
        )
    }

    return (
        <Container className="py-4">
            <Card>
                <CardBody>
                    <CardHeader tag="h2" className="mb-4">
                        Engagement Breakdown by User
                    </CardHeader>
                    {data && data.length > 0 ? (
                        <Table striped hover responsive>
                            <thead>
                                <tr>
                                    <th>User Name</th>
                                    <th>Screen Name</th>
                                    <th>Total Tweets</th>
                                    <th>Simple %</th>
                                    <th>Retweet %</th>
                                    <th>Quote %</th>
                                    <th>Reply %</th>
                                </tr>
                            </thead>
                            <tbody>
                                {data.map((item) => (
                                    <tr key={item.screen_name}>
                                        <td>{item.user_name}</td>
                                        <td>{item.screen_name}</td>
                                        <td>{item.total_tweets}</td>
                                        <td>{item.simple_percent.toFixed(2)}%</td>
                                        <td>{item.retweet_percent.toFixed(2)}%</td>
                                        <td>{item.quote_percent.toFixed(2)}%</td>
                                        <td>{item.reply_percent.toFixed(2)}%</td>
                                    </tr>
                                ))}
                            </tbody>
                        </Table>
                    ) : (
                        <p>No engagement data available.</p>
                    )}
                </CardBody>
            </Card>
        </Container>
    );
}

export default EngagementBreakdown;