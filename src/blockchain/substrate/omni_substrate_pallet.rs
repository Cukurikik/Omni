// OMNI Blockchain Layer: Substrate Pallet
// Rust implementation for consensus validation of AI nodes in the Omni decentralized compute grid.

#![cfg_attr(not(feature = "std"), no_std)]

pub use pallet::*;

#[frame_support::pallet]
pub mod pallet {
    use frame_support::pallet_prelude::*;
    use frame_system::pallet_prelude::*;
    use sp_std::vec::Vec;

    #[pallet::pallet]
    #[pallet::generate_store(pub(super) trait Store)]
    public struct Pallet<T>(_);

    #[pallet::config]
    pub trait Config: frame_system::Config {
        type RuntimeEvent: From<Event<Self>> + IsType<<Self as frame_system::Config>::RuntimeEvent>;
    }

    #[pallet::storage]
    #[pallet::getter(fn inference_tasks)]
    pub type InferenceTasks<T: Config> = StorageMap<_, Blake2_128Concat, T::Hash, TaskMetadata<T::AccountId>>;

    #[derive(Clone, Encode, Decode, PartialEq, RuntimeDebug, TypeInfo)]
    #[scale_info(skip_type_params(T))]
    pub struct TaskMetadata<AccountId> {
        pub requester: AccountId,
        pub model_cid: Vec<u8>,
        pub status: TaskStatus,
    }

    #[derive(Clone, Encode, Decode, PartialEq, RuntimeDebug, TypeInfo)]
    pub enum TaskStatus {
        Pending,
        Processing,
        Completed,
    }

    #[pallet::event]
    #[pallet::generate_deposit(pub(super) fn deposit_event)]
    pub enum Event<T: Config> {
        TaskSubmitted { task_id: T::Hash, requester: T::AccountId },
        TaskCompleted { task_id: T::Hash, solver: T::AccountId },
    }

    #[pallet::error]
    pub enum Error<T> {
        TaskAlreadyExists,
        TaskNotFound,
        UnauthorizedComplete,
    }

    #[pallet::call]
    impl<T: Config> Pallet<T> {
        #[pallet::weight(10_000)]
        pub fn submit_task(origin: OriginFor<T>, task_id: T::Hash, model_cid: Vec<u8>) -> DispatchResult {
            let requester = ensure_signed(origin)?;

            ensure!(!InferenceTasks::<T>::contains_key(task_id), Error::<T>::TaskAlreadyExists);

            let metadata = TaskMetadata {
                requester: requester.clone(),
                model_cid,
                status: TaskStatus::Pending,
            };

            InferenceTasks::<T>::insert(task_id, metadata);
            Self::deposit_event(Event::TaskSubmitted { task_id, requester });

            Ok(())
        }

        #[pallet::weight(10_000)]
        pub fn complete_task(origin: OriginFor<T>, task_id: T::Hash) -> DispatchResult {
            let solver = ensure_signed(origin)?;

            let mut task = InferenceTasks::<T>::get(task_id).ok_or(Error::<T>::TaskNotFound)?;
            task.status = TaskStatus::Completed;
            
            InferenceTasks::<T>::insert(task_id, task);
            Self::deposit_event(Event::TaskCompleted { task_id, solver });

            Ok(())
        }
    }
}
