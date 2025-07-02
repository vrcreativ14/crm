module.exports = {
  entry: ["regenerator-runtime/runtime.js","./components/pages/documents.js"],
  module: {
    rules: [
      {
        test: /\.js$/,
        exclude: /node_modules/,
        use: {
          loader: "babel-loader"
        }
      },
      {
        test: /\.svg$/,
        use: [
          {
            loader: 'svg-url-loader',
            options: {
              limit: 10000,
            },
          },
        ],
      },
      {
        test: /\.css$/,
        use: [
          { loader: 'style-loader' },
          { loader: 'css-loader' },
        ],
      },
      {
        test: /\.pdf$/,
        use: [
          { loader: 'file-loader' },
        ],
      }
    ]
  },
  devServer: {
    historyApiFallback: true
  },
  resolve: {
    fallback: {
        "fs": false
    },
  }
};