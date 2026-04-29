import React from 'react';
import { useQuery } from '@tanstack/react-query';
import {
    Container,
    Table,
    Spinner,
    Alert,
    Card,
    CardBody,
    CardTitle,
} from 'reactstrap';
import axios from 'axios';

type TopCountry = {
    country: string;
    tweet_count: number;
};

const fetchTopCountries = async (): Promise<TopCountry[]> => {
    const response = await axios.get<TopCountry[]>('/top-countries');

    return response.data.sort((a, b) => b.tweet_count - a.tweet_count);
};

export const TopCountries = (): React.JSX.Element => {
    const {
        data: countries,
        isLoading,
        isError,
        error,
    } = useQuery<TopCountry[], Error>({
        queryKey: ['top-countries'],
        queryFn: fetchTopCountries,
    });

    if (isLoading) {
        return (
            <Container className="mt-4 text-center">
                <Spinner />
                <p className="mt-2">Loading top countries (This may take awhile...)</p>
            </Container>
        );
    }

    if (isError) {
        return (
            <Container className="mt-4">
                <Alert color="danger">
                    Failed to load top countries: {error.message}
                </Alert>
            </Container>
        );
    }

    return (
        <Container className="mt-4">
            <Card>
                <CardBody>
                    <CardTitle tag="h2" className="mb-4">
                        Top Countries by Tweet Count
                    </CardTitle>

                    <Table striped hover responsive>
                        <thead>
                            <tr>
                                <th>#</th>
                                <th>Country</th>
                                <th>Tweet Count</th>
                            </tr>
                        </thead>
                        <tbody>
                            {countries?.map((country, index) => (
                                <tr key={country.country}>
                                    <th scope="row">{index + 1}</th>
                                    <td>{country.country}</td>
                                    <td>{country.tweet_count.toLocaleString()}</td>
                                </tr>
                            ))}
                        </tbody>
                    </Table>
                </CardBody>
            </Card>
        </Container>
    );
};

export default TopCountries;