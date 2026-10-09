import { defineConfig, globalIgnores } from 'eslint/config';
import tseslint from 'typescript-eslint';

export default defineConfig(globalIgnores(['design/', '_discard/', '_reserve/']), {
  files: ['**/*.ts'],
  extends: [tseslint.configs.recommendedTypeChecked],
  languageOptions: {
    parserOptions: {
      projectService: true,
      tsconfigRootDir: import.meta.dirname,
    },
  },
  rules: {
    // node:test's test() and describe() return promises that the runner awaits itself.
    '@typescript-eslint/no-floating-promises': [
      'error',
      {
        allowForKnownSafeCalls: [
          { from: 'package', package: 'node:test', name: ['describe', 'test'] },
        ],
      },
    ],
  },
});
