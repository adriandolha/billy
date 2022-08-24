import { DataGrid } from '@mui/x-data-grid';


export default function SimpleTable({ columns, rows, rowCount}) {

    return (
        <div style={{ height: 650, width: '100%' }}>
            <DataGrid
                rows={rows}
                columns={columns}
                rowCount={rowCount}
                rowsPerPageOptions={[20]}
                checkboxSelection={false}
            />
        </div>
    );
}
