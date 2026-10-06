import { theme } from 'antd';
import type { ThemeConfig } from 'antd';

/** Mundo monocromo: tinta como primario; el color queda para estados funcionales.
 * El negativo es estricto: en oscuro los tokens antd también se invierten. */
export const MONO = {
  ink: '#141412',
  paper: '#FAFAF8',
  negative: '#111110',
  negative2: '#1B1B18',
  negativeText: '#F2F1EC',
} as const;

export function getAntdTheme(dark: boolean): ThemeConfig {
  // En el negativo, el primario se invierte como todo el sistema: tinta -> papel
  const primary = dark ? MONO.negativeText : MONO.ink;
  const superficie = dark ? MONO.negative2 : MONO.paper;
  return {
    algorithm: dark ? theme.darkAlgorithm : theme.defaultAlgorithm,
    token: {
      colorPrimary: primary,
      colorLink: primary,
      colorInfo: primary,
      colorSuccess: '#15803d',
      colorWarning: '#b45309',
      colorError: '#b91c1c',
      colorTextBase: dark ? MONO.negativeText : MONO.ink,
      colorTextLightSolid: dark ? MONO.negative : '#FFFFFF',
      colorBgContainer: superficie,
      colorBgElevated: superficie,
      borderRadius: 2,
      fontFamily:
        'ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, sans-serif',
      fontSize: 13,
    },
    components: {
      Table: {
        headerBg: dark ? MONO.negative : '#F2F1EC',
        headerSplitColor: 'transparent',
        cellPaddingBlock: 10,
        fontSize: 12.5,
      },
      Button: { fontWeight: 600, primaryShadow: 'none', defaultShadow: 'none' },
      Tag: { borderRadiusSM: 2 },
      Modal: { titleFontSize: 16 },
      Card: { borderRadiusLG: 2 },
      Input: { borderRadius: 2 },
      Select: { borderRadius: 2 },
      Form: { labelFontSize: 12 },
    },
  };
}
