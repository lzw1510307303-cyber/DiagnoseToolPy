// Compression mode selector component

import { Select } from 'antd';
import type { CompressType } from '../../types/log';

interface CompressionControlProps {
  value: CompressType;
  onChange: (value: CompressType) => void;
}

const COMPRESS_OPTIONS: { label: string; value: CompressType }[] = [
  { label: 'None (Show All)', value: 'none' },
  { label: 'By Message Content', value: 'message' },
  { label: 'By Thread ID', value: 'thread_id' },
  { label: 'Both (Thread + Message)', value: 'both' },
];

function CompressionControl({ value, onChange }: CompressionControlProps) {
  return (
    <Select<CompressType>
      value={value}
      onChange={onChange}
      options={COMPRESS_OPTIONS}
      style={{ width: 200 }}
      placeholder="Select compression mode"
    />
  );
}

export default CompressionControl;
