#[cfg(test)]
mod tests {
    use super::segment_writer::SegmentWriter;

    #[test]
    fn test_segment_writer() {
        let writer = SegmentWriter::new(100).unwrap();
        let res = writer.write_vector(&[1.0, 2.0, 3.0]);
        assert!(res.is_ok());
    }
}
