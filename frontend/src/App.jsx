import React, { useEffect, useState } from 'react';
import axios from 'axios';
import './App.css';

function App() {
    const [odds, setOdds] = useState([]);

    useEffect(() => {
        axios.get('http://127.0.0.1:5000/api/odds')
            .then(response => {
                setOdds(response.data);
            })
            .catch(error => {
                console.error('Error fetching data:', error);
            });
    }, []);

    const groupedOdds = odds.reduce((acc, match) => {
        if (!acc[match.sport]) {
            acc[match.sport] = [];
        }
        acc[match.sport].push(match);
        return acc;
    }, {});

    return (
        <div className="App">
            {Object.keys(groupedOdds).map(sport => (
                <div key={sport} className="sport-section">
                    <h2>{sport.toUpperCase()}</h2>
                    <table>
                        <thead>
                            <tr>
                                <th>Date</th>
                                <th>Team 1</th>
                                <th>Team 2</th>
                                <th>Team 1 Max Odds</th>
                                <th>Team 2 Max Odds</th>
                                <th>Coefficient</th>
                            </tr>
                        </thead>
                        <tbody>
                            {groupedOdds[sport].map(match => (
                                <tr key={match.date_time}>
                                    <td>{new Date(match.date_time).toLocaleString()}</td>
                                    <td>{match.team1}</td>
                                    <td>{match.team2}</td>
                                    <td>
                                        <a href={match.team1_max.url} target="_blank" rel="noopener noreferrer">
                                            {match.team1_max.bookie}
                                        </a> ({match.team1_max.odds})
                                    </td>
                                    <td>
                                        <a href={match.team2_max.url} target="_blank" rel="noopener noreferrer">
                                            {match.team2_max.bookie}
                                        </a> ({match.team2_max.odds})
                                    </td>
                                    <td>{match.coefficient.toFixed(3)}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            ))}
        </div>
    );
}

export default App;
