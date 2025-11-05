const path = require('path');
const HtmlWebpackPlugin = require('html-webpack-plugin');

module.exports = (env, argv) => {
  const isDevelopment = argv.mode === 'development';

  return {
    entry: './renderer/src/index.tsx',
    target: 'electron-renderer',
    output: {
      path: path.resolve(__dirname, 'dist/renderer'),
      filename: 'bundle.js',
      clean: true
    },
    resolve: {
      extensions: ['.ts', '.tsx', '.js', '.jsx', '.json'],
      alias: {
        '@renderer': path.resolve(__dirname, 'renderer/src'),
        '@shared': path.resolve(__dirname, 'shared'),
        '@main': path.resolve(__dirname, 'main')
      }
    },
    module: {
      rules: [
        {
          test: /\.tsx?$/,
          use: {
            loader: 'ts-loader',
            options: {
              configFile: 'tsconfig.renderer.json'
            }
          },
          exclude: /node_modules/
        },
        {
          test: /\.css$/,
          use: ['style-loader', 'css-loader']
        },
        {
          test: /\.(png|jpg|jpeg|gif|svg|ico|ttf|woff|woff2|eot)$/,
          type: 'asset/resource',
          generator: {
            filename: 'assets/[name][ext]'
          }
        }
      ]
    },
    plugins: [
      new HtmlWebpackPlugin({
        template: './renderer/index.html',
        filename: 'index.html'
      })
    ],
    devServer: {
      port: 3000,
      hot: true,
      static: {
        directory: path.join(__dirname, 'assets')
      }
    },
    devtool: isDevelopment ? 'source-map' : false,
    mode: argv.mode || 'development'
  };
};
