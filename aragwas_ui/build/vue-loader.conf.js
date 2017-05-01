var utils = require('./utils')
var config = require('../config')
var isProduction = process.env.NODE_ENV === 'production'

const loaders = utils.cssLoaders({
    sourceMap: isProduction
      ? config.build.productionSourceMap
      : config.dev.cssSourceMap,
    extract: isProduction
});
loaders['ts'] = 'ts-loader!tslint-loader';
module.exports = {
  loaders: loaders,
  esModule: true
}
