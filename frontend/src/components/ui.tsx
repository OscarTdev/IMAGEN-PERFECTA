import React from 'react';
import { Card, Skeleton, Result } from 'antd';

export const LoadingBlock: React.FC<{ rows?: number }> = ({ rows = 4 }) => (
  <Card variant="outlined">
    <Skeleton active paragraph={{ rows }} />
  </Card>
);

export const ErrorBlock: React.FC<{ message: string }> = ({ message }) => (
  <Result status="error" title="No se pudo cargar" subTitle={message} />
);
