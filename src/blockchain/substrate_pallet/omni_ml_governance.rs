// @omni-layer Blockchain | @omni-lang Rust (Substrate) | @omni-batch 17
// @omni-description Substrate pallet for on-chain ML model governance:
// model registration, staking-based validation, and inference disputes.

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
        type MaxModelNameLen: Get<u32>;
        #[pallet::constant]
        type MinStakeAmount: Get<u128>;
    }

    #[derive(Clone, Encode, Decode, PartialEq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
    #[scale_info(skip_type_params(T))]
    pub struct ModelRecord<T: Config> {
        pub owner: T::AccountId,
        pub name: BoundedVec<u8, T::MaxModelNameLen>,
        pub architecture: BoundedVec<u8, ConstU32<64>>,
        pub parameter_count: u64,
        pub ipfs_cid: BoundedVec<u8, ConstU32<128>>,
        pub stake: u128,
        pub inference_count: u64,
        pub accuracy_score: u32,  // basis points (0-10000)
        pub status: ModelStatus,
        pub registered_at: BlockNumberFor<T>,
    }

    #[derive(Clone, Encode, Decode, PartialEq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
    pub enum ModelStatus {
        Registered,
        Active,
        Disputed,
        Slashed,
        Retired,
    }

    #[derive(Clone, Encode, Decode, PartialEq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
    pub struct InferenceDispute<AccountId, BlockNumber> {
        pub challenger: AccountId,
        pub model_id: u64,
        pub reason: BoundedVec<u8, ConstU32<256>>,
        pub stake: u128,
        pub filed_at: BlockNumber,
        pub resolved: bool,
    }

    #[pallet::pallet]
    pub struct Pallet<T>(_);

    #[pallet::storage]
    pub type Models<T: Config> = StorageMap<_, Blake2_128Concat, u64, ModelRecord<T>>;

    #[pallet::storage]
    pub type NextModelId<T> = StorageValue<_, u64, ValueQuery>;

    #[pallet::storage]
    pub type Disputes<T: Config> = StorageMap<
        _, Blake2_128Concat, u64,
        InferenceDispute<T::AccountId, BlockNumberFor<T>>
    >;

    #[pallet::storage]
    pub type TotalInferences<T> = StorageValue<_, u64, ValueQuery>;

    #[pallet::event]
    #[pallet::generate_deposit(pub(super) fn deposit_event)]
    pub enum Event<T: Config> {
        ModelRegistered { model_id: u64, owner: T::AccountId },
        ModelActivated { model_id: u64 },
        InferenceRecorded { model_id: u64, count: u64 },
        DisputeFiled { model_id: u64, challenger: T::AccountId },
        DisputeResolved { model_id: u64, slashed: bool },
    }

    #[pallet::error]
    pub enum Error<T> {
        ModelNotFound,
        NotModelOwner,
        InsufficientStake,
        ModelAlreadyActive,
        ModelNotActive,
        DisputeAlreadyExists,
    }

    #[pallet::call]
    impl<T: Config> Pallet<T> {
        #[pallet::call_index(0)]
        #[pallet::weight(10_000)]
        pub fn register_model(
            origin: OriginFor<T>,
            name: BoundedVec<u8, T::MaxModelNameLen>,
            architecture: BoundedVec<u8, ConstU32<64>>,
            parameter_count: u64,
            ipfs_cid: BoundedVec<u8, ConstU32<128>>,
            stake: u128,
        ) -> DispatchResult {
            let who = ensure_signed(origin)?;
            ensure!(stake >= T::MinStakeAmount::get(), Error::<T>::InsufficientStake);

            let model_id = NextModelId::<T>::get();
            let block = <frame_system::Pallet<T>>::block_number();

            let model = ModelRecord {
                owner: who.clone(),
                name, architecture, parameter_count, ipfs_cid,
                stake, inference_count: 0, accuracy_score: 0,
                status: ModelStatus::Registered,
                registered_at: block,
            };

            Models::<T>::insert(model_id, model);
            NextModelId::<T>::put(model_id + 1);
            Self::deposit_event(Event::ModelRegistered { model_id, owner: who });
            Ok(())
        }

        #[pallet::call_index(1)]
        #[pallet::weight(5_000)]
        pub fn activate_model(origin: OriginFor<T>, model_id: u64) -> DispatchResult {
            let who = ensure_signed(origin)?;
            Models::<T>::try_mutate(model_id, |maybe_model| {
                let model = maybe_model.as_mut().ok_or(Error::<T>::ModelNotFound)?;
                ensure!(model.owner == who, Error::<T>::NotModelOwner);
                ensure!(model.status == ModelStatus::Registered, Error::<T>::ModelAlreadyActive);
                model.status = ModelStatus::Active;
                Self::deposit_event(Event::ModelActivated { model_id });
                Ok(())
            })
        }

        #[pallet::call_index(2)]
        #[pallet::weight(3_000)]
        pub fn record_inference(origin: OriginFor<T>, model_id: u64) -> DispatchResult {
            ensure_signed(origin)?;
            Models::<T>::try_mutate(model_id, |maybe_model| {
                let model = maybe_model.as_mut().ok_or(Error::<T>::ModelNotFound)?;
                ensure!(model.status == ModelStatus::Active, Error::<T>::ModelNotActive);
                model.inference_count += 1;
                TotalInferences::<T>::mutate(|t| *t += 1);
                Self::deposit_event(Event::InferenceRecorded { model_id, count: model.inference_count });
                Ok(())
            })
        }
    }
}
