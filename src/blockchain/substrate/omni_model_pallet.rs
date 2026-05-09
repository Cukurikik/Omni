// OMNI Blockchain Layer — Rust Substrate Pallet for Model Registry
// Substrate runtime module for on-chain AI model governance.

#![cfg_attr(not(feature = "std"), no_std)]

pub use pallet::*;

#[frame_support::pallet]
pub mod pallet {
    use frame_support::pallet_prelude::*;
    use frame_system::pallet_prelude::*;
    use sp_std::vec::Vec;

    #[pallet::config]
    pub trait Config: frame_system::Config {
        type RuntimeEvent: From<Event<Self>> + IsType<<Self as frame_system::Config>::RuntimeEvent>;
        #[pallet::constant]
        type MaxNameLength: Get<u32>;
        #[pallet::constant]
        type MaxModelCount: Get<u32>;
    }

    #[derive(Clone, Encode, Decode, PartialEq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
    #[scale_info(skip_type_params(T))]
    pub struct ModelInfo<T: Config> {
        pub owner: T::AccountId,
        pub name: BoundedVec<u8, T::MaxNameLength>,
        pub version: BoundedVec<u8, ConstU32<32>>,
        pub ipfs_hash: BoundedVec<u8, ConstU32<64>>,
        pub parameter_count: u64,
        pub is_active: bool,
        pub total_inferences: u64,
        pub created_block: BlockNumberFor<T>,
    }

    #[pallet::pallet]
    pub struct Pallet<T>(_);

    #[pallet::storage]
    pub type Models<T: Config> = StorageMap<_, Blake2_128Concat, u32, ModelInfo<T>>;

    #[pallet::storage]
    pub type NextModelId<T: Config> = StorageValue<_, u32, ValueQuery>;

    #[pallet::storage]
    pub type ModelCount<T: Config> = StorageValue<_, u32, ValueQuery>;

    #[pallet::event]
    #[pallet::generate_deposit(pub(super) fn deposit_event)]
    pub enum Event<T: Config> {
        ModelRegistered { id: u32, owner: T::AccountId },
        ModelDeactivated { id: u32 },
        InferenceRecorded { id: u32, count: u64 },
    }

    #[pallet::error]
    pub enum Error<T> {
        ModelNotFound,
        NotModelOwner,
        ModelAlreadyInactive,
        TooManyModels,
        NameTooLong,
    }

    #[pallet::call]
    impl<T: Config> Pallet<T> {
        #[pallet::call_index(0)]
        #[pallet::weight(10_000)]
        pub fn register_model(
            origin: OriginFor<T>,
            name: Vec<u8>,
            version: Vec<u8>,
            ipfs_hash: Vec<u8>,
            parameter_count: u64,
        ) -> DispatchResult {
            let who = ensure_signed(origin)?;
            let count = ModelCount::<T>::get();
            ensure!(count < T::MaxModelCount::get(), Error::<T>::TooManyModels);

            let bounded_name: BoundedVec<u8, T::MaxNameLength> =
                name.try_into().map_err(|_| Error::<T>::NameTooLong)?;
            let bounded_version: BoundedVec<u8, ConstU32<32>> =
                version.try_into().map_err(|_| Error::<T>::NameTooLong)?;
            let bounded_hash: BoundedVec<u8, ConstU32<64>> =
                ipfs_hash.try_into().map_err(|_| Error::<T>::NameTooLong)?;

            let id = NextModelId::<T>::get();
            let model = ModelInfo::<T> {
                owner: who.clone(),
                name: bounded_name,
                version: bounded_version,
                ipfs_hash: bounded_hash,
                parameter_count,
                is_active: true,
                total_inferences: 0,
                created_block: <frame_system::Pallet<T>>::block_number(),
            };

            Models::<T>::insert(id, model);
            NextModelId::<T>::put(id + 1);
            ModelCount::<T>::put(count + 1);
            Self::deposit_event(Event::ModelRegistered { id, owner: who });
            Ok(())
        }

        #[pallet::call_index(1)]
        #[pallet::weight(5_000)]
        pub fn deactivate_model(origin: OriginFor<T>, id: u32) -> DispatchResult {
            let who = ensure_signed(origin)?;
            Models::<T>::try_mutate(id, |maybe_model| -> DispatchResult {
                let model = maybe_model.as_mut().ok_or(Error::<T>::ModelNotFound)?;
                ensure!(model.owner == who, Error::<T>::NotModelOwner);
                ensure!(model.is_active, Error::<T>::ModelAlreadyInactive);
                model.is_active = false;
                Self::deposit_event(Event::ModelDeactivated { id });
                Ok(())
            })
        }

        #[pallet::call_index(2)]
        #[pallet::weight(3_000)]
        pub fn record_inference(origin: OriginFor<T>, id: u32) -> DispatchResult {
            ensure_signed(origin)?;
            Models::<T>::try_mutate(id, |maybe_model| -> DispatchResult {
                let model = maybe_model.as_mut().ok_or(Error::<T>::ModelNotFound)?;
                model.total_inferences = model.total_inferences.saturating_add(1);
                Self::deposit_event(Event::InferenceRecorded { id, count: model.total_inferences });
                Ok(())
            })
        }
    }
}
