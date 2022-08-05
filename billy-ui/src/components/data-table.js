import { useMemo } from 'react';
import { DataGrid } from '@mui/x-data-grid';


export default function DataTable({ columns, rows, rowCount, page, pageSize, setPage, setPageSize }) {

    return (
        <div style={{ height: 650, width: '100%' }}>
            <DataGrid
                rows={rows}
                columns={columns}
                rowCount={rowCount}
                pageSize={pageSize}
                page={page}
                rowsPerPageOptions={[20]}
                // checkboxSelection
                paginationMode='server'
                onPageChange={(newPage) => setPage(newPage)}
                onPageSizeChange={(newPageSize) => setPageSize(newPageSize)}
            />
        </div>
    );
}
