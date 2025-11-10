const { override } = require('customize-cra');
const path = require('path');
const os = require('os');

// Helper function to safely normalize paths with exclamation marks
function safePathNormalize(pathString) {
  if (!pathString || typeof pathString !== 'string') {
    return pathString;
  }
  // Use absolute resolved path
  return path.resolve(pathString);
}

// Helper to convert string paths with ! to RegExp (Webpack accepts RegExp for include)
function pathToRegExp(pathString) {
  if (!pathString || typeof pathString !== 'string') {
    return pathString;
  }
  const normalized = path.resolve(pathString).replace(/\\/g, '/');
  // Escape special regex characters and create a pattern that matches the path
  const escaped = normalized.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  return new RegExp('^' + escaped);
}

// Recursive function to fix all string paths containing !
function fixPathsInObject(obj, depth = 0) {
  if (depth > 10) return obj; // Prevent infinite recursion
  
  if (Array.isArray(obj)) {
    return obj.map(item => fixPathsInObject(item, depth + 1));
  } else if (obj && typeof obj === 'object') {
    const fixed = {};
    for (const key in obj) {
      if (obj.hasOwnProperty(key)) {
        const value = obj[key];
        // Skip fixing loader paths - they should remain as strings
        if (key === 'loader' || key === 'use' || key === 'enforce') {
          fixed[key] = value;
        } else if (typeof value === 'string' && value.includes('!') && !value.includes('node_modules')) {
          // Only fix file paths, not loader syntax
          if (value.includes(path.sep) || value.startsWith('.')) {
            fixed[key] = path.resolve(value);
          } else {
            fixed[key] = value;
          }
        } else {
          fixed[key] = fixPathsInObject(value, depth + 1);
        }
      }
    }
    return fixed;
  }
  return obj;
}

module.exports = override(
  // Fix for paths containing exclamation marks
  (config) => {
    // Fix cache directory path - use temp directory if path contains !
    if (config.cache && config.cache.cacheDirectory) {
      const cacheDir = config.cache.cacheDirectory;
      if (typeof cacheDir === 'string' && cacheDir.includes('!')) {
        const tempCacheDir = path.join(os.tmpdir(), 'react-app-cache');
        config.cache.cacheDirectory = tempCacheDir;
        console.log(`Cache directory changed to: ${tempCacheDir}`);
      }
    }

    // Fix output path - use temp build directory if path contains !
    if (config.output) {
      const outputPath = config.output.path;
      if (typeof outputPath === 'string' && outputPath.includes('!')) {
        const tempBuildDir = path.join(os.tmpdir(), 'react-app-build');
        config.output.path = tempBuildDir;
        console.log(`Build output directory changed to: ${tempBuildDir}`);
      }
    }

    // Fix module rules includes - convert strings with ! to RegExp
    if (config.module && config.module.rules) {
      const fixIncludePath = (includeValue) => {
        if (Array.isArray(includeValue)) {
          return includeValue.map(fixIncludePath);
        } else if (typeof includeValue === 'string' && includeValue.includes('!')) {
          // Only convert file paths, not loader paths
          if (includeValue.includes(path.sep) || includeValue.startsWith('.')) {
            return pathToRegExp(includeValue);
          }
          return includeValue;
        }
        return includeValue;
      };

      config.module.rules.forEach((rule) => {
        if (rule.oneOf) {
          rule.oneOf.forEach((oneOfRule) => {
            if (oneOfRule.include) {
              oneOfRule.include = fixIncludePath(oneOfRule.include);
            }
            // Fix loader paths that might contain !
            if (oneOfRule.loader && typeof oneOfRule.loader === 'string' && oneOfRule.loader.includes('!') && oneOfRule.loader.includes(path.sep)) {
              oneOfRule.loader = path.resolve(oneOfRule.loader);
            }
          });
        } else {
          if (rule.include) {
            rule.include = fixIncludePath(rule.include);
          }
          if (rule.loader && typeof rule.loader === 'string' && rule.loader.includes('!') && rule.loader.includes(path.sep)) {
            rule.loader = path.resolve(rule.loader);
          }
        }
      });
    }

    return config;
  }
);

