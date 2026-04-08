import React, {useState, useEffect} from 'react';
import { CartesianGrid, Legend, Line, LineChart, Tooltip, XAxis, YAxis, ResponsiveContainer } from 'recharts';
import logo from './logo.svg';
import './App.css';

function App() {
  const [stockData, setStockData] = useState([]);
  const[loading, setLoading] = useState(true);
  const API_ENDPOINT = `${process.env.REACT_APP_API_URL}movers`;

  useEffect(() => {
    fetch(API_ENDPOINT)
    .then(response => response.json())
    .then((data) => {
      const formattedData = data.map(item => ({
        ...item,
        percentValue: parseFloat(item['Percent Change'])
      })).reverse();

      setStockData(formattedData);
      setLoading(false);
    })
    .catch((error) => console.error('Error fetching stocks', error));
  }, [API_ENDPOINT]);

  if (loading) return <div>Loading Market Movers</div>;

  return (
    <div className="App">
      <h1>7-Day Market Winners</h1>
        <div style={{ width: '100%', maxWidth: '800px', margin: '0 auto' }}>
        <ResponsiveContainer width="100%" height={400}>
          <LineChart data={stockData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="Date" />
            <YAxis label={{ value: '% Change', angle: -90, position: 'insideLeft' }} />
            <Tooltip />
            <Legend />
            {/* dataKey matches the key in your DynamoDB/Lambda response */}
            <Line 
              type="monotone" 
              dataKey="percentValue" 
              stroke="8884d8"
              name="Winner % Change" 
              strokeWidth={3}
              dot={{ r:6 }}
              activeDot={{ r:8 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

    <div className="card-container">
        {stockData.map((stock, index) => (
          <article key={index} className="card" style={{ border: stock.percentValue >= 0 ? '2px solid green' : '2px solid red' }}>
            <header>
              <h2>{stock['Ticker Symbol']}</h2>
            </header>
            <div className="content">
              <p>Date: {stock.Date}</p>
              <p>Move: {stock['Percent Change']}%</p>
              <p>Price: ${stock['Closing Price']}</p>
            </div>
          </article>
        ))}
      </div>
    </div>
  );
}
        

export default App;
