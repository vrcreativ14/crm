var path = require('path');
var webpack = require('webpack');

var config = {
    entry: ['./app/index.jsx'],
    output: {
        path: path.join(__dirname, 'dist'),
        filename: 'app.js'
    },
    resolve: {
        extensions: ['', '.js', '.jsx', '.json']
    },
    module: {
        loaders: [
            {
                test: /\.jsx?$/,
                loaders: ['react-hot', 'jsx-loader?insertPragma=React.DOM&harmony&presets[]=es2015,presets[]=react', 'babel?presets[]=es2015,presets[]=react'],
                exclude: /node_modules/,
            }
        ]
    },
    plugins: [
        new webpack.DefinePlugin({
            'process.env': {
                'NODE_ENV': JSON.stringify('production')
            }
        })
    ],
};

module.exports = config;
