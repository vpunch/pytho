import {
    createColumnHelper, getCoreRowModel, useReactTable, flexRender
} from '@tanstack/react-table';
import styled from 'styled-components';


const COLUMN_HELPER = createColumnHelper<any>()


const StyledTable = styled.table`
  margin-top: 2em;

  --column-gap: 1em;

  th {
    padding-left: var(--column-gap);
  }

  td {
    padding-left: var(--column-gap);
    max-width: 10em;
    text-overflow: ellipsis;
    overflow: hidden;
  }
`;

const Cell = styled.div`
  text-align: left;
`;


function Table({rows}: {rows: any[]}) {
    const columns = Object.keys(rows[0]).map(
        column => COLUMN_HELPER.accessor(row => row[column], {id: column})
    );

    const table = useReactTable({
        data: rows,
        columns,
        getCoreRowModel: getCoreRowModel()
    });

    const headerGroup = table.getHeaderGroups()[0]

    const headerRow = (
      <tr key={headerGroup.id}>
        {headerGroup.headers.map(header => (
          <th key={header.id}>
            <Cell>
              {flexRender(
                  header.column.columnDef.header, header.getContext())}
            </Cell>
          </th>
        ))}
      </tr>
    );

    const dataRows = table.getRowModel().rows.map(row => (
      <tr key={row.id}>
        {row.getAllCells().map(cell => (
          <td key={cell.id}>
            <Cell>{cell.getValue() as any}</Cell>
          </td>
        ))}
      </tr>
    ));

    return (
      <StyledTable>
        <thead>{headerRow}</thead>
        <tbody>{dataRows}</tbody>
      </StyledTable>
    );
}


export default Table;
