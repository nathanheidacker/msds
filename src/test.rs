use pyo3::prelude::*;

#[pyfunction]
pub fn test() -> PyResult<()> {
    Ok(())
}
