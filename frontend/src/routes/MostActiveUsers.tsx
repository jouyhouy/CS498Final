import React from 'react';
import axios from 'axios';
import { useQuery } from '@tanstack/react-query'
import { Container, Spinner, Table } from 'reactstrap';

interface ActiveUser {
    user_id: number;
    user_name: string;
    screen_name: string;
    tweet_count: number;
}

const getMostActiveUsers = async (): Promise<ActiveUser[]> => {
    try {
        const response = await axios.get('/most-active-user');
        return response.data;
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
    } catch (error: any) {
        throw new Error("An error occurred while fetching most active users", {
            cause: error,
        });
    }
}

const MostActiveUsers = (): React.JSX.Element => {
    const { data, error, isLoading } = useQuery<ActiveUser[]>({
        queryKey: ['most-active-users'],
        queryFn: getMostActiveUsers,
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
            <div className="alert alert-danger" role="alert">
                {error instanceof Error ? error.message : 'An unknown error occurred.'}
            </div>
        )
    }

    return (
        <Container className="py-4">
            <h2 className="mb-4">Most Active Users</h2>
            <Table striped hover responsive>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Username</th>
                        <th>Screen Name</th>
                        <th>Tweet Count</th>
                    </tr>
                </thead>
                <tbody>
                    {data?.map((user) => (
                        <tr key={user.user_id}>
                            <td>{user.user_id}</td>
                            <td>{user.user_name}</td>
                            <td>{user.screen_name}</td>
                            <td>{user.tweet_count}</td>
                        </tr>
                    ))}
                </tbody>
            </Table>
        </Container>
    )
}

export default MostActiveUsers;