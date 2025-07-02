const path = require('path');
const VueLoaderPlugin = require('vue-loader/lib/plugin');

const projectRoot = path.resolve(__dirname, '../../')

module.exports = {
    entry: {
        'auto_quoter': path.resolve(projectRoot, './auto_quoter/prebuild_static/js/index.js')
    },
    output: {
        filename: '[name].js',
        path: path.resolve(projectRoot, './common_static/dist')
    },
    module: {
        rules: [
            {
                test: /\.vue$/,
                loader: 'vue-loader'
            },
            {
                test: /\.css$/,
                use: [
                    'style-loader',
                    'css-loader'
                ]
            }
        ]
    },
    plugins: [
        new VueLoaderPlugin(),
    ]
};