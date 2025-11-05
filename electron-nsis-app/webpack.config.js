const path = require('path');
const HtmlWebpackPlugin = require('html-webpack-plugin');
const webpack = require('webpack');

module.exports = (env, argv) => {
  const isDevelopment = argv.mode === 'development';

  return {
    entry: './renderer/src/index.tsx',
    target: 'electron-renderer',
    output: {
      path: path.resolve(__dirname, 'dist/renderer'),
      filename: '[name].bundle.js',
      chunkFilename: '[name].chunk.js',
      clean: true
    },
    resolve: {
      extensions: ['.ts', '.tsx', '.js', '.jsx', '.json'],
      alias: {
        '@': path.resolve(__dirname, 'renderer/src'),
        '@renderer': path.resolve(__dirname, 'renderer/src'),
        '@shared': path.resolve(__dirname, 'shared'),
        '@main': path.resolve(__dirname, 'main'),
        '@components': path.resolve(__dirname, 'renderer/src/components'),
        '@icons': path.resolve(__dirname, 'renderer/src/components/icons')
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
      }),
      // Fix per "global is not defined" error in Webpack 5
      new webpack.DefinePlugin({
        global: 'window',
      })
    ],
    devServer: {
      port: 3000,
      hot: true,
      static: {
        directory: path.join(__dirname, 'assets')
      }
    },
    optimization: {
      usedExports: true, // Tree-shaking per rimuovere icone non utilizzate
      sideEffects: false, // Assume no side effects per tree-shaking ottimale
      splitChunks: {
        chunks: 'all',
        cacheGroups: {
          // Separa lucide-react in un chunk separato per caching migliore
          lucideReact: {
            test: /[\\/]node_modules[\\/]lucide-react[\\/]/,
            name: 'lucide-icons',
            priority: 10
          },
          vendor: {
            test: /[\\/]node_modules[\\/]/,
            name: 'vendors',
            priority: 5
          }
        }
      }
    },
    devtool: isDevelopment ? 'source-map' : false,
    mode: argv.mode || 'development'
  };
};
