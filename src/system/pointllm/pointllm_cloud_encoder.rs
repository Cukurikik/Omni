/// PointLLM — 3D Point Cloud Encoder (ownership-safe)
/// Farthest Point Sampling + grouping for point cloud feature extraction

pub struct OmniResult<T, E> { pub value: Option<T>, pub error: Option<E> }

pub struct PointCloud {
    pub points: Vec<[f32; 3]>,  // [N, 3] XYZ coordinates
    pub colors: Vec<[f32; 3]>,  // [N, 3] RGB colors
}

pub struct FPSSampler {
    num_samples: u32,
    radius: f32,
}

impl FPSSampler {
    const MAX_POINTS: u32 = 10_000_000;
    const MAX_SAMPLES: u32 = 65536;

    pub fn new(num_samples: u32, radius: f32) -> OmniResult<Self, String> {
        if num_samples > Self::MAX_SAMPLES {
            return OmniResult { value: None, error: Some("Samples exceed 64K".into()) };
        }
        if radius <= 0.0 || radius > 100.0 {
            return OmniResult { value: None, error: Some("Radius must be in (0, 100]".into()) };
        }
        OmniResult { value: Some(Self { num_samples, radius }), error: None }
    }

    pub fn sample(&self, cloud: &PointCloud) -> OmniResult<Vec<usize>, String> {
        let n = cloud.points.len();
        if n == 0 { return OmniResult { value: None, error: Some("Empty point cloud".into()) }; }
        if n > Self::MAX_POINTS as usize {
            return OmniResult { value: None, error: Some("Points exceed 10M".into()) };
        }
        let k = (self.num_samples as usize).min(n);
        let mut selected = Vec::with_capacity(k);
        let mut distances = vec![f32::MAX; n];
        selected.push(0usize);
        for _ in 1..k {
            let last = selected[selected.len() - 1];
            let lp = &cloud.points[last];
            for j in 0..n {
                let p = &cloud.points[j];
                let d = (p[0]-lp[0]).powi(2) + (p[1]-lp[1]).powi(2) + (p[2]-lp[2]).powi(2);
                if d < distances[j] { distances[j] = d; }
            }
            let farthest = distances.iter().enumerate()
                .max_by(|a, b| a.1.partial_cmp(b.1).unwrap()).unwrap().0;
            selected.push(farthest);
        }
        OmniResult { value: Some(selected), error: None }
    }
}
