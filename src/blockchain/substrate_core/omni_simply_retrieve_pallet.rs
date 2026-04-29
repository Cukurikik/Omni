#![cfg_attr(not(feature = "std"), no_std)]

// Omni SimplyRetrieve Pallet in Rust (Substrate)
// Core consensus bridging for indexing retrieval hashes.

pub use pallet::*;

#[frame_support::pallet]
pub mod pallet {
    use frame_support::pallet_prelude::*;
    use frame_system::pallet_prelude::*;

    #[pallet::pallet]
    pub struct Pallet<T>(_);

    #[pallet::config]
    pub trait Config: frame_system::Config {}

    #[pallet::error]
    pub enum Error<T> {
        EmptyHash,
    }

    #[pallet::storage]
    #[pallet::getter(fn retrieve_hashes)]
    pub type RetrieveHashes<T: Config> = StorageMap<_, Blake2_128Concat, T::AccountId, [u8; 32]>;

    #[pallet::call]
    impl<T: Config> Pallet<T> {
        #[pallet::weight(10_000)]
        pub fn store_retrieval_hash(origin: OriginFor<T>, hash: [u8; 32]) -> DispatchResult {
            let who = ensure_signed(origin)?;
            
            // Deterministic state update with monadic error handling
            if hash == [0u8; 32] {
                return Err(Error::<T>::EmptyHash.into());
            }
            
            RetrieveHashes::<T>::insert(&who, hash);
            Ok(())
        }
    }
}
