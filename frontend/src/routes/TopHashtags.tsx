import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { Alert, Card, CardBody, CardTitle, Container, Spinner, Table } from 'reactstrap';
import axios from 'axios';

interface Hashtag {
    hashtag: string;
    count: number;
}

const fetchTopHashtags = async (): Promise<Hashtag[]> => {
    try {
        const response = await axios.get('/top-hashtags');
        if (response.status !== 200) {
            throw new Error('Failed to fetch top hashtags');
        }
        return response.data as Hashtag[];
        // Catch any network or parsing errors
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
    } catch (error: any) {
        throw new Error('Failed to fetch top hashtags', { cause: error });
    }
};

const TopHashtags = (): React.JSX.Element => {
    const { data, isLoading, isError } = useQuery<Hashtag[]>({
        queryKey: ['top-hashtags'],
        queryFn: fetchTopHashtags
    });

    if (isLoading) return (
        <div className="d-flex flex-column flex-grow-1 justify-content-center align-items-center w-100 py-5">
            <Spinner color="primary" />
            <p>Loading... (this may take a moment)</p>
        </div>
    );

    if (isError) return <Alert color="danger">Error fetching top hashtags.</Alert>;

    return (
        <Container className="mt-4">
            <Card>
                <CardBody>
                    <CardTitle tag="h2" className="mb-4">
                        Top Hashtags by Count
                    </CardTitle>
                    <Table striped hover responsive>
                        <thead>
                            <tr>
                                <th>Hashtag</th>
                                <th>Count</th>
                            </tr>
                        </thead>
                        <tbody>
                            {data?.map((hashtag, index) => (
                                <tr key={index}>
                                    <td>#{hashtag.hashtag}</td>
                                    <td>{hashtag.count}</td>
                                </tr>
                            ))}
                        </tbody>
                    </Table>
                </CardBody>
            </Card>
        </Container>
    )
}

export default TopHashtags;