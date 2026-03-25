export default function Layout() {
  return (
    <div className="m-0 flex h-screen overflow-y-hidden bg-green-600 p-0">
      {/* Left icon nav */}
      <div className="p-0">
        <div className="pt-[10px] pr-[10px] pb-[10px] pl-[10px]">
          <div className="custom-height-main-menu relative flex w-[100px] flex-col justify-between rounded-sm bg-white shadow-[0px_1px_2px_0px_rgba(0,0,0,0.10)]">
            <div className="flex flex-1 items-center justify-center">
              {/* Logo */}
              <div className="absolute top-[26px] left-[16px] h-[28px] w-[68px] cursor-pointer bg-white pl-[22px]">
                <img src="/assets/images/neso/dap_logo.svg" alt="Logo" />
              </div>

              {/* Divider */}
              <div className="absolute top-[80px] h-px w-14 rounded-[1px] bg-[#9DA6D3] opacity-20"></div>

              {/* Nav icons */}
              <div className="absolute top-[6.7rem] inline-flex flex-col items-center justify-start gap-2.5">
                <a href="/">
                  <div className="relative h-[60px] w-[120px]">
                    <div
                      className="absolute left-[46px] z-50"
                      style={{ top: '17px', width: '32px', height: '28px' }}
                    >
                      <img src="/assets/images/neso/home.svg" />
                    </div>
                  </div>
                </a>

                <a aria-current="page" className="active" href="/home/datacatalogue">
                  <div className="relative h-[60px] w-[120px]">
                    <div className="absolute top-0 left-0 z-50 h-[60px] w-[120px] bg-[#0F1A48] shadow-[0px_10px_20px_0px_rgba(16,26,73,0.20)]"></div>
                    <div
                      className="absolute left-[46px] z-50"
                      style={{ top: '14px', width: '28px', height: '34px' }}
                    >
                      <img src="/assets/images/neso/catalogue_active.svg" />
                    </div>
                  </div>
                </a>

                <a href="/home/products">
                  <div className="relative h-[60px] w-[120px]">
                    <div
                      className="absolute left-[46px] z-50"
                      style={{ top: '17px', width: '32px', height: '28px' }}
                    >
                      <img src="/assets/images/neso/asr.svg" />
                    </div>
                  </div>
                </a>

                <a href="/home/knowledgebase">
                  <div className="relative h-[60px] w-[120px]">
                    <div
                      className="absolute left-[46px] z-50"
                      style={{ top: '17px', width: '34px', height: '23px' }}
                    >
                      <img src="/assets/images/neso/knowledge.svg" />
                    </div>
                  </div>
                </a>

                <div className="h-px w-14 rounded-[1px] bg-[#411133] opacity-20"></div>
              </div>

              {/* Bottom logo */}
              <div className="mt-auto mb-[20px]">
                <div className="ml-[10px] flex w-[5rem] flex-col justify-end gap-[0.3125rem]">
                  <a href="/">
                    <img
                      src="/assets/images/neso/neso_logo.svg"
                      alt="react logo"
                      className="h-[1.625rem] w-[5rem]"
                    />
                  </a>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Main content area */}
      <div className="flex w-full flex-col">
        {/* Top bar */}
        <div className="bottom-2 mr-[30px] w-full bg-red-600 pt-[10px] pb-[24px]">
          <div className="flex w-full">
            <div className="flex w-full">
              <div className="w-3/4 rounded-sm p-0"></div>
              <div className="w-1/4 p-0">
                <div className="flex flex-row justify-end">
                  <div className="inline-flex flex-col items-end justify-start gap-2.5 rounded-sm bg-[#F5F5F5] pt-1.5 pr-2.5 pb-1.5">
                    <div className="inline-flex items-center justify-end gap-2.5 self-stretch">
                      <div className="inline-flex flex-col items-end justify-center">
                        <div className="text-dap-blue justify-start text-right text-base font-light">
                          Devesh
                        </div>
                      </div>
                      <div className="flex h-10 items-center justify-start gap-1.5">
                        <div className="relative h-[36px] w-[37px]">
                          <div className="bg-dap-blue flex h-[36px] w-[36px] items-center justify-center rounded-full font-bold text-white">
                            DS
                          </div>
                        </div>
                        <div className="relative h-[14px] w-[14px]">
                          <i className="pi pi-chevron-down"></i>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Content below top bar */}
        <div>
          <div className="flex w-full">
            {/* Sub-navigation sidebar */}
            <div className="ml-[30px]">
              <div className="custom-height-submenu flex w-[190px] flex-col justify-around">
                <div className="flex-1">
                  <div className="flex flex-col items-start justify-start gap-3 self-stretch">
                    <div className="inline-flex items-start justify-start gap-2.5 px-3.5">
                      <div className="justify-start text-lg leading-none font-bold tracking-tight text-black">
                        Data Catalogue
                      </div>
                    </div>
                    <div className="flex flex-col items-start justify-start gap-1.5 self-stretch">
                      <a
                        aria-current="page"
                        className="bg-dap-blue active inline-flex min-h-8 cursor-pointer items-center justify-start gap-2.5 self-stretch pr-2.5 shadow-[0px_10px_20px_0px_rgba(16,26,73,0.20)]"
                        href="/home/datacatalogue"
                      >
                        <div className="active inline-flex min-h-8 w-full items-center justify-start gap-2.5 self-stretch pr-4.5">
                          <div className="relative h-8 min-h-8 w-[5px]">
                            <div className="absolute top-0 left-0 h-8 w-[5px] bg-white/0"></div>
                          </div>
                          <div className="flex-1 justify-start text-base font-normal text-white">
                            All Assets
                          </div>
                        </div>
                      </a>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Main panel */}
            <div className="relative ml-[40px] flex w-full flex-col">
              {/* Breadcrumbs */}
              <div className="absolute top-0 left-0 inline-flex min-h-7 items-center justify-start gap-2.5">
                <div className="flex-1 self-stretch py-[5px]">
                  <div className="breadcrumbs"></div>
                </div>
              </div>

              <div>
                <div className="flex w-full flex-row gap-4">
                  {/* Results column */}
                  <div className="relative mt-[48px] mr-[20px] flex h-8.5 w-[61.8%] flex-col gap-4">
                    <div className="custom-height-center scroll-bar result-container gap-2 bg-[#F5F5F5]">
                      {/* Search bar */}
                      <div className="absolute top-[-7rem] flex w-full flex-row items-center justify-between">
                        <div className="relative flex w-full flex-col gap-4">
                          <div className="flex flex-row-reverse">
                            <div className="w-full">
                              <input
                                type="text"
                                placeholder="Search here"
                                className="h-9 w-full rounded-sm border-none pr-[2.5rem] text-center text-sm font-medium shadow-[0px_1px_2px_0px_rgba(0,0,0,0.09)] outline outline-1 outline-offset-[-1px] outline-none placeholder:text-center placeholder:text-[#C7C7C7] hover:shadow-[0px_4px_10px_0px_rgba(0,0,0,0.12)] hover:placeholder:text-[#818181] focus:ring-0 focus:outline-none"
                                defaultValue="ukgov_territorial_greenhouse_gas_emissions_by_fuels_aviation_and_shipping_bun"
                              />
                            </div>
                            <div className="absolute mt-2 mr-4 cursor-pointer">
                              <svg
                                width="18"
                                height="18"
                                viewBox="0 0 18 18"
                                fill="none"
                                xmlns="http://www.w3.org/2000/svg"
                              >
                                <path
                                  d="M3 3L15 15M15 3L3 15"
                                  stroke="black"
                                  strokeWidth="1.5"
                                  strokeLinecap="round"
                                  strokeLinejoin="round"
                                />
                              </svg>
                            </div>
                          </div>
                        </div>
                      </div>

                      {/* Sort / Filter */}
                      <div className="absolute -top-12 flex w-full flex-row items-center justify-between">
                        <div className="flex flex-row items-center"></div>
                        <div className="flex flex-row gap-2.5">
                          <div className="relative inline-block text-right">
                            <button className="flex items-center gap-2 rounded bg-gray-100 px-4 py-2 hover:cursor-pointer">
                              <span>Sort</span>
                              <svg
                                width="10"
                                height="6"
                                viewBox="0 0 10 6"
                                fill="none"
                                xmlns="http://www.w3.org/2000/svg"
                                style={{ transform: 'rotate(0deg)', transition: 'transform 0.2s' }}
                              >
                                <path
                                  d="M0.75 0.75L4.75 4.75L8.75 0.75"
                                  stroke="#101A49"
                                  strokeWidth="1.5"
                                  strokeLinecap="round"
                                />
                              </svg>
                            </button>
                          </div>
                          <div className="relative inline-block text-right">
                            <button className="flex items-center gap-2 rounded bg-gray-100 px-4 py-2 hover:cursor-pointer">
                              <span>Filter</span>
                              <svg
                                width="10"
                                height="6"
                                viewBox="0 0 10 6"
                                fill="none"
                                xmlns="http://www.w3.org/2000/svg"
                                style={{ transform: 'rotate(0deg)', transition: 'transform 0.2s' }}
                              >
                                <path
                                  d="M0.75 0.75L4.75 4.75L8.75 0.75"
                                  stroke="#101A49"
                                  strokeWidth="1.5"
                                  strokeLinecap="round"
                                />
                              </svg>
                            </button>
                          </div>
                        </div>
                      </div>

                      {/* Results list */}
                      <div>
                        <div className="mb-[14px] inline-flex h-9 w-[897px] items-center justify-start gap-2.5 rounded-sm">
                          <div className="relative h-4 w-4">
                            <svg
                              width="18"
                              height="18"
                              viewBox="0 0 18 18"
                              fill="none"
                              xmlns="http://www.w3.org/2000/svg"
                            >
                              <path
                                d="M3 5V0.5H10.5L16 6V17.5H3M3 9H7M3 13H7"
                                stroke="black"
                                strokeLinejoin="round"
                              />
                            </svg>
                          </div>
                          <div className="font-['Poppins'] text-lg leading-4 font-bold tracking-tight text-black">
                            Dataset Instance
                          </div>
                          <div className="w-64 self-stretch bg-white/0"></div>
                        </div>

                        {/* Result card */}
                        <div className="hover:border-Support-Light-Gery-2 relative mb-3.5 flex w-full cursor-pointer flex-col items-start justify-start gap-1 self-stretch border-b bg-white p-5 shadow-[0px_1px_2px_0px_rgba(0,0,0,0.10)] hover:rounded-sm hover:shadow-[0px_6px_14px_0px_rgba(0,0,0,0.10)]">
                          <div className="absolute top-0 left-0 w-[5px]">
                            <div className="absolute top-0 left-0 w-[5px] bg-white/0"></div>
                          </div>
                          <div className="flex h-5 w-full items-center justify-start gap-2.5 self-stretch">
                            <div className="relative h-4 w-4">
                              <svg
                                width="18"
                                height="18"
                                viewBox="0 0 18 18"
                                fill="none"
                                xmlns="http://www.w3.org/2000/svg"
                              >
                                <path
                                  d="M3 5V0.5H10.5L16 6V17.5H3M3 9H7M3 13H7"
                                  stroke="black"
                                  strokeLinejoin="round"
                                />
                              </svg>
                            </div>
                            <div className="line-clamp-1 justify-start text-base leading-none font-semibold tracking-tight whitespace-pre text-black uppercase">
                              <mark className="font-bold">
                                ukgov_territorial_greenhouse_gas_emissions_by_fuels_aviation_and_shipping_bun
                              </mark>
                              kers_in_mtco2e
                            </div>
                            <div className="bg-dap-tag-grey flex items-center justify-start gap-2.5 rounded-sm px-2.5 py-0.5">
                              <div className="text-Main-Black justify-center font-['Roboto_Mono'] text-xs font-bold uppercase">
                                XLSX
                              </div>
                            </div>
                            <div className="flex-1 self-stretch bg-white/0 opacity-0"></div>
                          </div>
                          <div className="flex h-5 items-start justify-start gap-3 self-stretch overflow-hidden">
                            <div className="flex h-5 items-start justify-start gap-3 self-stretch">
                              <div className="w-4 self-stretch bg-white/0"></div>
                              <div className="line-clamp-1 flex-1 justify-start pr-14 text-xs leading-normal font-normal text-black">
                                Greenhouse gas emissions arising from the use of fuels from UK
                                international aviation and shipping bunkers in million tonnes carbon
                                dioxide equivalent (MtCO2e) 1990-2022
                              </div>
                            </div>
                          </div>
                          <div className="flex h-5 items-center justify-start gap-3 self-stretch">
                            <div className="w-4 self-stretch opacity-0"></div>
                            <div className="justify-center text-[10px] font-normal text-black">
                              01.02.2026
                            </div>
                            <div className="text-dap-blue-bright justify-center text-[10px] font-bold">
                              653751e6-f973-47b7-809c-7f08a4540d80
                            </div>
                            <div className="flex-1 self-stretch bg-white/0 opacity-0"></div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Detail panel */}
                  <div className="custom-height-right scroll-bar mr-[40px] w-[38.2%] bg-white">
                    <div className="inline-flex w-full flex-col items-start justify-start gap-5 p-5">
                      <div className="border-mid-grey inline-flex h-9 items-center justify-center gap-5 self-stretch border-b p-2.5">
                        <div className="flex flex-1 items-center justify-start gap-2.5 self-stretch">
                          <div className="justify-start text-xl leading-none font-bold text-black">
                            Dataset Instance
                          </div>
                        </div>
                      </div>

                      <div className="flex flex-col items-start justify-start gap-1.5 self-stretch">
                        <div className="inline-flex min-h-10 items-center justify-start gap-3 self-stretch rounded-md py-1">
                          <div className="flex h-5 w-4 items-center justify-between">
                            <div className="relative h-4 w-4">
                              <svg
                                width="18"
                                height="18"
                                viewBox="0 0 18 18"
                                fill="none"
                                xmlns="http://www.w3.org/2000/svg"
                              >
                                <path
                                  d="M3 5V0.5H10.5L16 6V17.5H3M3 9H7M3 13H7"
                                  stroke="black"
                                  strokeLinejoin="round"
                                />
                              </svg>
                            </div>
                          </div>
                          <div className="w-[1rem] flex-1 justify-start text-base leading-tight font-semibold break-words whitespace-normal text-black uppercase">
                            OCF_SOLAR_FORECAST
                          </div>
                        </div>
                        <div className="inline-flex items-start justify-start gap-2 self-stretch pr-2.5 pl-7">
                          <div className="w-[1rem] flex-1 justify-start text-sm leading-none font-normal break-words whitespace-normal text-black">
                            This will contain the national solar forecasts and return the most recent
                            forecast for each target time for all Grid Supply Points (GSPs)
                          </div>
                        </div>
                      </div>

                      <div className="bg-light-grey inline-flex min-h-8 items-center justify-start gap-2.5 self-stretch">
                        <div className="flex w-36 items-center justify-end gap-1.5 rounded-md">
                          <div className="justify-center text-right text-sm font-normal text-black">
                            Dataset Format
                          </div>
                        </div>
                        <div className="flex flex-1 items-center justify-start gap-3 rounded-md pr-2.5">
                          <div className="justify-center text-base font-semibold text-black uppercase">
                            CSV
                          </div>
                          <div className="flex-1 self-stretch bg-white opacity-0"></div>
                        </div>
                      </div>

                      <div className="flex flex-col items-start justify-start gap-2.5 self-stretch pl-2.5">
                        <div className="inline-flex items-center justify-between self-stretch">
                          <div className="justify-start text-base font-semibold text-black uppercase">
                            Data Taxonomy
                          </div>
                        </div>
                        <div className="inline-flex items-start justify-start self-stretch">
                          <div className="flex w-7 items-center justify-start gap-2.5 self-stretch">
                            <div className="border-mid-grey flex-1 self-stretch border-r"></div>
                          </div>
                          <div className="inline-flex flex-1 flex-col items-start justify-start gap-1 border-l">
                            <div className="inline-flex min-h-8 items-center justify-start gap-2.5 self-stretch pl-2.5 ring-2 ring-transparent hover:ring-gray-200">
                              <div className="flex w-32 items-center justify-end gap-1.5 rounded-md">
                                <div className="justify-center text-right text-sm font-normal text-black">
                                  Data Domain
                                </div>
                              </div>
                              <div className="flex flex-1 items-center justify-start gap-3 rounded-md pr-2.5">
                                <div className="justify-center text-base font-semibold text-black">
                                  Long-Term Forecasting &amp; Planning
                                </div>
                                <div className="min-w-7 flex-1 self-stretch bg-white opacity-0"></div>
                              </div>
                            </div>
                            <div className="inline-flex min-h-8 items-center justify-start gap-2.5 self-stretch pl-2.5 ring-2 ring-transparent hover:ring-gray-200">
                              <div className="flex w-32 items-center justify-end gap-1.5 rounded-md">
                                <div className="justify-center text-right text-sm font-normal text-black">
                                  Data Sub-domain
                                </div>
                              </div>
                              <div className="flex flex-1 items-center justify-start gap-3 rounded-md pr-2.5">
                                <div className="justify-center text-base font-semibold text-black">
                                  Long-Term Scenario
                                </div>
                                <div className="min-w-7 flex-1 self-stretch bg-white opacity-0"></div>
                              </div>
                            </div>
                            <div className="inline-flex min-h-8 items-center justify-start gap-2.5 self-stretch pl-2.5 ring-2 ring-transparent hover:ring-gray-200">
                              <div className="flex w-32 items-center justify-end gap-1.5 rounded-md">
                                <div className="justify-center text-right text-sm font-normal text-black">
                                  Dataset Group
                                </div>
                              </div>
                              <div className="flex flex-1 items-center justify-start gap-3 rounded-md pr-2.5">
                                <div className="justify-center text-base font-semibold text-black">
                                  Forecast - Long-Term Scenario
                                </div>
                                <div className="min-w-7 flex-1 self-stretch bg-white opacity-0"></div>
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>

                      <div className="border-mid-grey inline-flex h-9 items-center justify-center gap-5 self-stretch border-b p-2.5">
                        <div className="flex flex-1 items-center justify-start gap-2.5 self-stretch">
                          <div className="justify-start text-xl leading-none font-bold text-black">
                            Metadata
                          </div>
                        </div>
                        <div className="inline-flex h-4 w-4 cursor-pointer flex-col items-start justify-start gap-2.5">
                          <svg
                            width="18"
                            height="18"
                            viewBox="0 0 18 18"
                            fill="none"
                            xmlns="http://www.w3.org/2000/svg"
                          >
                            <rect x="0.5" y="0.5" width="17" height="17" stroke="#C7C7C7" />
                            <rect
                              x="4.5"
                              y="3.5"
                              width="9"
                              height="11"
                              rx="0.5"
                              fill=""
                              stroke="black"
                            />
                          </svg>
                        </div>
                      </div>

                      <div className="bg-light-grey inline-flex h-8 items-center justify-start gap-2.5 self-stretch">
                        <div className="flex w-36 items-center justify-end gap-1.5 rounded-md">
                          <div className="justify-center text-right text-sm font-normal text-black">
                            Data Classification
                          </div>
                        </div>
                        <div className="flex h-8 flex-1 items-center justify-start gap-3 rounded-md pr-2.5">
                          <div className="justify-center text-base font-semibold text-black">
                            General
                          </div>
                          <div className="relative h-2.5 w-2.5">
                            <div
                              className="absolute top-0 left-0 h-2.5 w-2.5 rounded-full shadow-[0px_1px_2px_0px_rgba(0,0,0,0.10)] outline outline-1 outline-white"
                              style={{ backgroundColor: 'rgb(255, 221, 0)' }}
                            ></div>
                          </div>
                          <div className="flex-1 self-stretch bg-white opacity-0"></div>
                        </div>
                      </div>

                      <div className="inline-flex min-h-8 items-center justify-start gap-2.5 self-stretch bg-white">
                        <div className="flex w-36 items-center justify-end gap-1.5 rounded-md">
                          <div className="justify-center text-right text-sm font-normal text-black">
                            Sharing Status
                          </div>
                        </div>
                        <div className="flex flex-1 items-center justify-start gap-3 rounded-md pr-2.5">
                          <div className="justify-center text-base font-semibold text-black">
                            Not Open – Must be triaged before sharing
                          </div>
                          <div className="flex-1 self-stretch bg-white opacity-0"></div>
                        </div>
                      </div>

                      <div className="bg-light-grey inline-flex min-h-8 items-center justify-start gap-2.5 self-stretch">
                        <div className="flex h-8 w-36 items-center justify-end gap-1.5 rounded-md">
                          <div className="justify-center text-right text-sm font-normal text-black">
                            Updated
                          </div>
                        </div>
                        <div className="flex h-8 flex-1 items-center justify-start gap-3 rounded-md pr-2.5">
                          <div className="justify-center text-base font-semibold text-black"></div>
                          <div className="flex-1 self-stretch bg-white opacity-0"></div>
                        </div>
                      </div>

                      <div className="inline-flex h-11 w-full flex-col items-end justify-start gap-2 pb-5">
                        <div className="text-dap-blue-bright cursor-pointer justify-start text-base font-semibold underline">
                          More Metadata
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="z-0"></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
