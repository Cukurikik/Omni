FROM scratch
COPY omni_unikernel.ukl /
ENTRYPOINT ["/omni_unikernel.ukl"]
